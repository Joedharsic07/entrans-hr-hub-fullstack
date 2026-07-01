import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';
import { ServiceService } from '../Service/service.service';
import { LoginService } from '../../component/service/login.service';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.component.html',
  styleUrl: './user-list.component.css'
})
export class UserListComponent implements OnInit, OnDestroy {

  users: any[] = [];
  loading = false;
  search = '';
  page = 1;
  totalPages = 1;
  totalCount = 0;
  readonly pageSize = 15;

  // Delete confirm modal
  showDeleteModal = false;
  deleteTarget: any = null;
  deleteLoading = false;
  deleteError = '';

  // Status toggle feedback
  statusMsg: { [id: number]: string } = {};

  // Create User modal
  showCreateModal = false;
  createForm!: FormGroup;
  createLoading = false;
  createError = '';
  createSuccess = '';

  private search$ = new Subject<string>();
  private destroy$ = new Subject<void>();

  constructor(
    public service: ServiceService,
    public router: Router,
    private fb: FormBuilder,
    private loginService: LoginService
  ) {}

  ngOnInit(): void {
    this.createForm = this.fb.group({
      first_name: ['', [Validators.required, Validators.minLength(2)]],
      last_name: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      designation: [''],
      role: ['user', Validators.required]
    });
    this.loadUsers();

    this.search$.pipe(
      debounceTime(350),
      distinctUntilChanged(),
      takeUntil(this.destroy$)
    ).subscribe(() => {
      this.page = 1;
      this.loadUsers();
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadUsers(): void {
    this.loading = true;
    const params: any = { page: this.page, page_size: this.pageSize };
    if (this.search.trim()) params.search = this.search.trim();

    this.service.getAdminUsers(params).subscribe({
      next: (res: any) => {
        this.users = res.users;
        this.totalCount = res.count;
        this.totalPages = res.total_pages;
        this.page = res.current_page;
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  onSearchChange(): void {
    this.search$.next(this.search);
  }

  clearSearch(): void {
    this.search = '';
    this.page = 1;
    this.loadUsers();
  }

  goToPage(p: number): void {
    if (p < 1 || p > this.totalPages) return;
    this.page = p;
    this.loadUsers();
  }

  toggleActive(user: any): void {
    const newStatus = !user.is_active;
    this.service.updateUserStatus(user.id, newStatus).subscribe({
      next: () => {
        user.is_active = newStatus;
        this.statusMsg[user.id] = newStatus ? 'Activated' : 'Deactivated';
        setTimeout(() => delete this.statusMsg[user.id], 2000);
      },
      error: (err: any) => {
        this.statusMsg[user.id] = err.error?.error || 'Failed to update';
        setTimeout(() => delete this.statusMsg[user.id], 3000);
      }
    });
  }

  confirmDelete(user: any): void {
    this.deleteTarget = user;
    this.deleteError = '';
    this.showDeleteModal = true;
  }

  cancelDelete(): void {
    this.showDeleteModal = false;
    this.deleteTarget = null;
  }

  doDelete(): void {
    if (!this.deleteTarget) return;
    this.deleteLoading = true;
    this.deleteError = '';

    this.service.deleteAdminUser(this.deleteTarget.id).subscribe({
      next: () => {
        this.deleteLoading = false;
        this.showDeleteModal = false;
        this.deleteTarget = null;
        this.loadUsers();
      },
      error: (err: any) => {
        this.deleteLoading = false;
        this.deleteError = err.error?.error || 'Failed to delete user.';
      }
    });
  }

  get pageNumbers(): number[] {
    const total = this.totalPages;
    const cur = this.page;
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const pages: number[] = [];
    for (let i = 1; i <= total; i++) {
      if (i === 1 || i === total || (i >= cur - 2 && i <= cur + 2)) {
        pages.push(i);
      } else if (pages[pages.length - 1] !== -1) {
        pages.push(-1);
      }
    }
    return pages;
  }

  goBack(): void {
    this.router.navigate(['/admin']);
  }

  openCreateModal(): void {
    this.createForm.reset({ role: 'user' });
    this.createError = '';
    this.createSuccess = '';
    this.showCreateModal = true;
  }

  closeCreateModal(): void {
    this.showCreateModal = false;
  }

  submitCreateUser(): void {
    if (this.createForm.invalid) return;
    this.createLoading = true;
    this.createError = '';
    this.createSuccess = '';

    this.loginService.createUser(this.createForm.value).subscribe({
      next: (res: any) => {
        this.createLoading = false;
        this.createSuccess = res.message || 'User created successfully.';
        this.loadUsers();
        setTimeout(() => this.closeCreateModal(), 1800);
      },
      error: (err: any) => {
        this.createLoading = false;
        this.createError = err.error?.error || 'Failed to create user.';
      }
    });
  }
}
