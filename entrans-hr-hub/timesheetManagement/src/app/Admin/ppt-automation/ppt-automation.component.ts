import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ServiceService } from '../Service/service.service';
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
