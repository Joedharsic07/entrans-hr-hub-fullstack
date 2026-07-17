import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ServiceService } from '@core/services/api/admin.service';
import { saveAs } from 'file-saver';
import { HotToastService } from '@ngneat/hot-toast';
@Component({
  selector: 'app-ppt-automation',
  templateUrl: './ppt-automation.component.html',
  styleUrl: './ppt-automation.component.css'
})
export class PptAutomationComponent {
  pptForm: any;
  formSubmitted = false;
  errorMessage = '';
  recentGenerations: any[] = [];
  isLoadingRecent = false;

  currentPage: number = 1;
  pageSize: number = 5;

  get totalPages(): number {
    return Math.max(1, Math.ceil((this.recentGenerations?.length || 0) / this.pageSize));
  }

  get paginatedGenerations(): any[] {
    if (!this.recentGenerations) return [];
    const start = (this.currentPage - 1) * this.pageSize;
    return this.recentGenerations.slice(start, start + this.pageSize);
  }

  get pageNumbers(): number[] {
    const total = this.totalPages;
    const cur = this.currentPage;
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const pages: number[] = [];
    for (let i = 1; i <= total; i++) {
      if (i === 1 || i === total || (i >= cur - 2 && i <= cur + 2)) {
        pages.push(i);
      } else if (pages.length > 0 && pages[pages.length - 1] !== -1) {
        pages.push(-1);
      }
    }
    return pages;
  }

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }

  constructor(private fb: FormBuilder, private Service: ServiceService, private toster: HotToastService) {
    this.initializeForm();
    this.loadRecentGenerations();
  }

  initializeForm() {
    this.pptForm = this.fb.group({
      name: ['', [Validators.required]],
      years: ['', [Validators.required, Validators.min(1), Validators.max(4)]],
      file: [null]
    });
  }

  loadRecentGenerations() {
    this.isLoadingRecent = true;
    this.Service.getRecentPpts().subscribe({
      next: (res: any) => {
        this.recentGenerations = res;
        this.isLoadingRecent = false;
      },
      error: () => this.isLoadingRecent = false
    });
  }

  getSlideBackground(): string {
    const yearsValue = this.pptForm.get('years')?.value;
    let year = parseInt(yearsValue, 10);
    if (isNaN(year) || year < 1) {
      year = 1;
    } else if (year > 4) {
      year = 4; // Max 4 slides in our template array
    }
    return `assets/ppt_bgs/bg_${year}.jpg`;
  }

  onFileChange(event: any) {
    if (event.target.files.length > 0) {
      const file = event.target.files[0];
      this.pptForm.patchValue({
        file: file
      });
    }
  }

  onSubmit() {
    this.formSubmitted = true;

    if (this.pptForm.valid) {
      const formData = new FormData();
      formData.append('name', this.pptForm.get('name')?.value);
      formData.append('years', this.pptForm.get('years')?.value);
      formData.append('file', this.pptForm.get('file')?.value);
      const name = this.pptForm.get('name')?.value

      this.Service.generatePpt(formData).subscribe({
        next: (response: Blob) => {
          saveAs(response, `${name}_Anniversary_Presentation.pptx`);
          this.toster.success("Presentation Generated And Downloaded Successfully");
          this.loadRecentGenerations();
        },
        error: (error) => {
          console.error('Error generating PPT:', error);
          this.errorMessage = 'Failed to generate presentation. Please try again.';
        }
      });
    }
  }
}
