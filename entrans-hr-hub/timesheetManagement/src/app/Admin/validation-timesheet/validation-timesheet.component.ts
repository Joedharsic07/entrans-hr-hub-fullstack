import { Component } from '@angular/core';
import { ServiceService } from '../Service/service.service';
import { HotToastService } from '@ngneat/hot-toast';

interface Entry {
  top_status?: any;
  user_id: number;
  user_name: string;
  user_email: string;
  project_id: number;
  project_name: string;
  selected?: boolean;
  loading?: boolean;
  status?: 'success' | 'error';
  error?: string;
  result?: any;
  validation_status?: string;
  timesheet_validations?: any[];
  needs_rerun?: boolean;
  emailLoading?: boolean;
}

@Component({
  selector: 'app-validation-timesheet',
  templateUrl: './validation-timesheet.component.html',
  styleUrl: './validation-timesheet.component.css'
})
export class ValidationTimesheetComponent {
  data: Entry[] = [];
  selectedMonth = new Date().toISOString().slice(0, 7);
  loading = false;
  isFetchingData = false;
  selectAll = false;

  constructor(private timesheetService: ServiceService, private toastrservice: HotToastService) {}

  ngOnInit() {
    this.fetchData();
  }

  fetchData() {
    if (!this.selectedMonth) return;
    this.isFetchingData = true;
    this.data = [];
    const [year, month] = this.selectedMonth.split('-');
    this.timesheetService.getUserProjects(month, year).subscribe({
      next: (res) => {
        const items: Entry[] = [];

        const processUser = (user: any) => {
          if (!user.projects || user.projects.length === 0) {
            items.push({
              user_id: user.user_id,
              user_name: user.user_name,
              user_email: user.user_email,
              project_id: 0,
              project_name: 'No Project',
              validation_status: 'Pending',
              selected: false,
              needs_rerun: false,
              error: undefined
            });
          } else {
            user.projects.forEach((proj: any) => {
              const validations = proj.timesheet_validations || [];

              const hasChanges = validations.some((entry: any) => entry.changed === true);

              const errorFlags = validations
                .filter((entry: any) => entry.Status === 'Invalid' && entry.Flag)
                .map((entry: any) => this.formatEntryFlag(entry));

              items.push({
                user_id: user.user_id,
                user_name: user.user_name,
                user_email: user.user_email,
                project_id: proj.project_id,
                project_name: proj.project_name,
                validation_status: proj.validation_status,
                selected: false,
                needs_rerun: hasChanges,
                error: errorFlags.length > 0 ? errorFlags.join('\n') : undefined
              });
            });
          }
        };

        Array.isArray(res) ? res.forEach(processUser) : processUser(res);
        this.data = items;
        this.isFetchingData = false;
      },
      error: (err) => {
        console.error('Error fetching data:', err);
        this.isFetchingData = false;
      }
    });
  }
  validateEntry(entry: Entry) {
    if (!this.selectedMonth) return;
    entry.loading = true;
    entry.status = undefined;
    entry.error = undefined;

    const [year, month] = this.selectedMonth.split('-');
    const payload = {
      user_project_map: { [entry.user_id]: [entry.project_id] },
      month,
      year
    };

    this.timesheetService.validationTimesheet(payload).subscribe(
      () => {
        entry.result = 'Validated';
        entry.status = 'success';
        entry.loading = false;
      },
      err => {
        entry.error = err.error?.error || 'Validation failed';
        entry.status = 'error';
        entry.loading = false;
      }
    );
  }

toggleSelectAll() {
    this.data.forEach(e => (e.selected = this.selectAll));
  }

  onRowCheckboxChange() {
    this.selectAll = this.data.length > 0 && this.data.every(e => e.selected);
  }

  formatEntryFlag(entry: any): string {
  const date = entry.Date || entry.date;
  const flag = entry.Flag || '';

  const isTimesheetMissing = /no\s+timesheet/i.test(flag);

  if (!date || isTimesheetMissing) {
    return flag;
  }

  return `${date}: ${flag}`;
}

 validateSelected() {
  if (!this.selectedMonth) return;
  const [year, month] = this.selectedMonth.split('-');

  const map: any = {};
  this.data.forEach(e => {
    if (e.selected && e.project_id) {
      e.loading = true;
      e.status = undefined;
      e.error = undefined;
      map[e.user_id] = map[e.user_id] || [];
      map[e.user_id].push(e.project_id);
    }
  });

  if (!Object.keys(map).length) return;

  this.loading = true;
  this.timesheetService.validationTimesheet({ user_project_map: map, month, year })
    .subscribe(
      res => {
       const topStatus = res.status;

        this.data.forEach(e => {
          if (e.selected) {
            const uid = e.user_id;
            const pid = e.project_id;
            const validated = res.validated_data?.[uid]?.[pid] || [];

            const summary = res.validation_summary?.[uid]?.[pid] || [];

            const hasInvalidSummary = summary.some((s: any) => s.Status === 'Invalid');

            const invalidEntries = validated.filter((entry: any) => entry.Status === 'Invalid');

            e.result = `${validated.length} entries`;
            e.status = 'success';
            e.top_status = topStatus;
            if (hasInvalidSummary || invalidEntries.length > 0) {
              e.status = 'error';

              const summaryFlags = summary
                .filter((s: any) => s.Status === 'Invalid' && s.Flag)
                .map((s: any) => s.Flag);

              const entryFlags = invalidEntries.map((entry: any) => this.formatEntryFlag(entry));

              e.error = [...summaryFlags, ...entryFlags].join('\n') || 'Validation issues found.';
            } else {
              e.status = 'success';
              e.error = '';
            }

            e.loading = false;
          }
        });

        this.loading = false;
        this.fetchData();
      },
      err => {
        this.data.forEach(e => {
          if (e.selected) {
            e.error = err.error?.error || 'Validation failed';
            e.status = 'error';
            e.loading = false;
          }
        });
        this.loading = false;
      }
    );
}

pushEmail(entry: Entry) {
  if (!this.selectedMonth || !entry.project_id) return;

  const [year, month] = this.selectedMonth.split('-');

  entry.emailLoading = true;
  const payload = {
    user_project_map: {
      [entry.user_id]: [entry.project_id]
    },
    month,
    year
  };

  this.timesheetService.pushEmail(payload).subscribe({
    next: (res: any) => {
      entry.emailLoading = false;

      const sent: string[] = res?.sent || [];
      const failed: string[] = res?.failed || [];

      // Successful sends
      if (sent.length > 0) {
        this.toastrservice.success(
          `Email sent to ${entry.user_name} for project "${entry.project_name}"`);
      }

      // No flagged entries (warning prefix ⚠️)
      const noFlags = failed.filter((m: string) => m.startsWith('⚠️'));
      if (noFlags.length > 0) {
        this.toastrservice.info(
          `No issues found — nothing to email for ${entry.user_name} on "${entry.project_name}"`);
      }

      // Actual SMTP failures (error prefix ❌)
      const smtpErrors = failed.filter((m: string) => m.startsWith('❌'));
      if (smtpErrors.length > 0) {
        this.toastrservice.error(
          `Failed to send email to ${entry.user_name}`);
      }
    },
    error: () => {
      entry.emailLoading = false;
      this.toastrservice.error(
        'Failed to send email.');
    }
  });
}
  hasSelection(): boolean {
    return this.data.some(e => e.selected);
  }

  // --- New Computed Properties and Helpers for Mockup UI ---

  get totalEmployees(): number {
    return this.data.length;
  }

  get validatedCount(): number {
    return this.data.filter(e => this.getEntryStatus(e) === 'Valid').length;
  }

  get warningsCount(): number {
    return this.data.filter(e => this.getEntryStatus(e) === 'Warning').length;
  }

  get missingCount(): number {
    return this.data.filter(e => this.getEntryStatus(e) === 'Missing').length;
  }

  getEntryStatus(e: Entry): 'Valid' | 'Warning' | 'Missing' | 'Pending' {
    if (e.status === 'success' && !e.error) return 'Valid';
    if (e.status === 'error' || e.error) {
      if (e.error?.toLowerCase().includes('no timesheet')) return 'Missing';
      return 'Warning';
    }
    
    // Fallback to initial validation_status
    if (e.validation_status === 'Success' && !e.error) return 'Valid';
    if (e.validation_status === 'Success' && e.error) return 'Warning';
    if (e.validation_status === 'Needs rerun' && e.error) return 'Warning';
    if (e.validation_status === 'Needs to be run' || e.error?.toLowerCase().includes('no timesheet')) return 'Missing';

    return 'Pending';
  }

  getUserInitials(name: string): string {
    if (!name) return 'U';
    const parts = name.split(' ');
    if (parts.length > 1) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  getAvatarColor(name: string): string {
    if (!name) return 'bg-slate-100 text-slate-700 border-slate-200';
    const colors = [
      'bg-red-100 text-red-700 border-red-200',
      'bg-orange-100 text-orange-700 border-orange-200',
      'bg-amber-100 text-amber-700 border-amber-200',
      'bg-green-100 text-green-700 border-green-200',
      'bg-emerald-100 text-emerald-700 border-emerald-200',
      'bg-teal-100 text-teal-700 border-teal-200',
      'bg-cyan-100 text-cyan-700 border-cyan-200',
      'bg-blue-100 text-blue-700 border-blue-200',
      'bg-indigo-100 text-indigo-700 border-indigo-200',
      'bg-violet-100 text-violet-700 border-violet-200',
      'bg-purple-100 text-purple-700 border-purple-200',
      'bg-fuchsia-100 text-fuchsia-700 border-fuchsia-200',
      'bg-pink-100 text-pink-700 border-pink-200',
      'bg-rose-100 text-rose-700 border-rose-200'
    ];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  }

  getWorkLogClass(e: Entry, day: string): string {
    const status = this.getEntryStatus(e);
    // Mock logic to display bubbles like the design
    if (status === 'Missing') {
      return 'bg-slate-100 text-slate-300 font-medium'; // mostly grey
    }
    if (status === 'Warning' && day === 'W') {
      return 'bg-red-100 text-red-500 flex items-center justify-center content-["!"]';
    }
    // Default blue for filled days
    return 'bg-blue-600 text-white';
  }
}
