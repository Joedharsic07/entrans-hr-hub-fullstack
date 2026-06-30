import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ServiceService } from '../Service/service.service';
import { saveAs } from 'file-saver'; 
import { ToastrService } from 'ngx-toastr';
@Component({
  selector: 'app-ppt-automation',
  templateUrl: './ppt-automation.component.html',
  styleUrl: './ppt-automation.component.css'
})
export class PptAutomationComponent {
pptForm: any;
  formSubmitted = false;
  errorMessage = '';

  constructor(private fb: FormBuilder, private Service: ServiceService, private toster:ToastrService) {
    this.initializeForm();
  }

  initializeForm() {
    this.pptForm = this.fb.group({
      name: ['', [Validators.required]],
      years: ['', [Validators.required, Validators.min(1)]],
      file: [null, [Validators.required]]
    });
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
      const name=this.pptForm.get('name')?.value
      
      this.Service.generatePpt(formData).subscribe({
        next: (response: Blob) => {
          saveAs(response, `${name}_Anniversary_Presentation.pptx`);
          this.toster.success("Presentation Generated And Downloaded Successfully")
            // this.pptForm.reset();
            // this.pptForm.markAsPristine();
            // this.pptForm.markAsUntouched();
        },
        error: (error) => {
          console.error('Error generating PPT:', error);
          this.errorMessage = 'Failed to generate presentation. Please try again.';
        }
      });
    }
  }
}
