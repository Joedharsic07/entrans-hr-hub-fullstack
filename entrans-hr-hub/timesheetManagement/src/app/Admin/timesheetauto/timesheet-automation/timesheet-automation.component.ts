import { Component } from '@angular/core';
import { ServiceService } from '../../Service/service.service';
import { HttpErrorResponse } from '@angular/common/http';
import { FormControl, FormGroup } from '@angular/forms';

interface ValidationSummaryItem {

  'S.No': string;
  'File Name': string;
  'Description': string;
  'Hours': string;
  'Review': string;
  'Date'?: string;       // Add optional properties
  'Employee'?: string;
  'Project'?: string;
  [key: string]: any;

}
interface EmailData {
  recipient_email: string;
  // subject: string;
  // body: string;
  json_data: any
  validation_summary?: ValidationSummaryItem[];
  validated_data?: ValidatedData;
}
interface ValidatedData {
  [key: string]: any[];
}
interface ValidatedDataItem {
  [key: string]: any; // Flexible structure for timesheet data
}

interface ValidationResponse {
  recipient_email: string;
  json_data: {
    file_name: string;
    validated_data: ValidatedData;
    validation_summary: ValidationSummaryItem[];
  };
}
interface TimesheetEntry {
  Client: string;
  Date: string;
  Description: string;
  Hours: string;
  Status: string;
  Flag: string;
}

@Component({
  selector: 'app-timesheet-automation',
  templateUrl: './timesheet-automation.component.html',
  styleUrls: ['./timesheet-automation.component.css']
})
export class TimesheetAutomationComponent {
  private readonly STORAGE_KEY = 'timesheet_validation_data';
  constructor(private service: ServiceService) { }
  emailForm: any;
  fileName: any

  validationResults: ValidationResponse | null = null;
  selectedFile: File | null = null;
  result: string | null = null;
  isLoading: boolean = false;
  formData: FormData | null = null;

  validationSummary: ValidationSummaryItem[] = [];
  validatedData: { [key: string]: ValidatedDataItem[] } = {};
  selectedUser: number = 0;
  selectedUserName: string = '';
  recipientEmail: string = '';
  emailSubject: string = '';
  emailBody: string = '';
  isSendingEmail: boolean = false;

  // Messages
  message: string = '';
  messageType: 'success' | 'error' | null = null;
  private messageTimeout: any;

  ngOnInit(): void {
    this.emailForm = new FormGroup({
      recipient_email: new FormControl(''),
    });
    const keys = Object.keys(this.validatedData);
    if (keys.length > 0) {
      this.selectedUserName = keys[0];
    }
    this.loadFromStorage();
    const savedData = localStorage.getItem('timesheet_validation_data');
  if (savedData) {
    try {
      const parsedData = JSON.parse(savedData);
      this.result = parsedData.result;
      this.fileName = parsedData.fileName;
      this.validatedData = parsedData.validatedData || {};
      this.validationSummary = parsedData.validationSummary || [];
      this.selectedUserName = parsedData.selectedUserName || '';
      
      // Load email data
      this.emailBody = parsedData.emailBody || '';
      this.emailSubject = parsedData.emailSubject || '';
      
      // Set first user as default if none selected
      const keys = Object.keys(this.validatedData);
      if (keys.length > 0 && !this.selectedUserName) {
        this.selectedUserName = keys[0];
      }
    } catch (e) {
      console.error('Error loading saved data', e);
      localStorage.removeItem('timesheet_validation_data');
    }
  }
  }
  getrecipientEmail() {
    return this.emailForm.get('recipient_email')?.value;
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0] as File;
    this.validationResults = null;
  }

  onSubmit(): void {
    if (!this.selectedFile) {
      this.result = 'Please select a file first';
      return;
    }

    this.isLoading = true;
    this.formData = new FormData();
    this.formData.append('timesheet_file', this.selectedFile);

    this.service.timesheetValidation(this.formData).subscribe({
      next: (response: any) => {
        this.result = response.result || 'Validation completed successfully';
        this.fileName = response.file_name
        // Process the response data
        if (response.validated_data) {
          this.validatedData = response.validated_data;
          this.validationResults = response
        } else if (response.validatedData) {
          this.validatedData = response.validatedData;
        }
        const keys = Object.keys(this.validatedData);
        if (keys.length > 0) {
          this.selectedUserName = keys[0];
        }

        if (response.validation_summary) {
          this.validationResults = null;
          this.validationSummary = response.validation_summary;
        } else if (response.validationSummary) {
          this.validationSummary = response.validationSummary;
        }
        this.saveToStorage();

        // Generate the email body after receiving the data
        this.generateEmailBody();
        this.isLoading = false;
      },
      error: (error: HttpErrorResponse) => {
        this.clearStorage();
        this.result = error.error?.message || 'Validation failed';
        this.validationSummary = [];
        this.validatedData = {};
        this.isLoading = false;
        console.error('Validation error:', error);
      }
    });
  }

  submitTimesheet(): void {
    if (!this.validatedData) {
      this.showMessage('No validation results to submit', 'error');
      return;
    }

    this.isLoading = true;
    this.service.sendValidationEmail(this.validatedData).subscribe({
      next: (response: any) => {
        this.showMessage(response.message || 'Timesheet submitted successfully', 'success');
        this.isLoading = false;
      },
      error: (error: HttpErrorResponse) => {
        this.showMessage(error.error?.message || 'Failed to submit timesheet', 'error');
        this.isLoading = false;
      }
    });
  }

  getSheetNames(): string[] {
    if (!this.validationResults?.json_data?.validated_data) return [];
    return Object.keys(this.validationResults.json_data.validated_data);
  }

  getSheetData(sheetName: string): TimesheetEntry[] {
    if (!this.validationResults?.json_data?.validated_data) return [];
    return this.validationResults.json_data.validated_data[sheetName] || [];
  }

  getKeys(obj: any): string[] {
    return Object.keys(obj);
  }

  getSummaryKeys(): string[] {
    if (this.validationSummary.length > 0) {
      return Object.keys(this.validationSummary[0]);
    }
    return [];
  }

  onUserSelectChange() {
  }

  sendEmail(): void {
    this.recipientEmail = this.getrecipientEmail()
    console.log(this.recipientEmail)
    if (!this.recipientEmail) {
      this.showMessage('Please enter a recipient email', 'error');
      return;
    }

    if (!this.validateEmail(this.recipientEmail)) {
      this.showMessage('Please enter a valid email address', 'error');
      return;
    }

    this.isSendingEmail = true;
    this.clearMessage();

    const emailData: EmailData = {
      recipient_email: this.recipientEmail,
      json_data: {
        "file_name": this.fileName,
        "validated_data": this.validatedData,
        "validation_summary": this.validationSummary
      }

    };

    this.service.sendValidationEmail(emailData).subscribe({
      next: (response: any) => {
        this.showMessage(response.message || 'Email sent successfully', 'success');
        this.isSendingEmail = false;
      },
      error: (error: HttpErrorResponse) => {
        this.showMessage(error.error?.message || 'Failed to send email', 'error');
        this.isSendingEmail = false;
      }
    });
  }
  private generateEmailBody(): void {
    let body = 'Timesheet Validation Results:\n\n';

    // Group validation issues by file/sheet
    const issuesBySheet: { [key: string]: ValidationSummaryItem[] } = {};

    this.validationSummary.forEach(item => {
      if (item.Review !== 'OK') {
        const sheetName = item['File Name'] || 'Unknown Sheet';
        if (!issuesBySheet[sheetName]) {
          issuesBySheet[sheetName] = [];
        }
        issuesBySheet[sheetName].push(item);
      }
    });

    // Process each sheet's issues
    for (const [sheetName, issues] of Object.entries(issuesBySheet)) {
      body += `Hello,\n`;
      body += 'The following errors were found in your timesheet submission: \n\n';
      this.emailSubject = sheetName
      body += `File name / Client - ${this.fileName}:\n`
    }

    for (const [sheetName, entries] of Object.entries(this.validatedData)) {
      const flaggedEntries = entries.filter((entry: any) => entry.Status && entry.Status.trim() !== 'Valid');
      body += `Total Issues Found: ${flaggedEntries.length}\n`

      if (flaggedEntries.length > 0) {
        body += `${sheetName}:\n`;


        flaggedEntries.forEach((entry: any) => {
          body += `Error/Warning:${entry.Status}`
          body += `Related Timesheet Row: {\n`;
          body += `  Date: ${entry.Date || 'N/A'}\n\n`;
          body += `  Description: ${entry.Description || 'N/A'}\n\n`;
          body += `  Hours: ${entry.Hours || 'N/A'}\n\n`;
          body += `}\n`;
          body += '----------------------------------------\n\n';
        });
        body += " Please review and correct the above entries as soon as possible."

      }

    }

    if (body === 'Timesheet Validation Results:\n\n') {
      body += 'No issues found. All timesheets are valid.';
    }

    this.emailBody = body;
    this.saveEmailDataToStorage();

  }
private saveEmailDataToStorage(): void {
    const currentData = localStorage.getItem('timesheet_validation_data');
    if (currentData) {
        const parsedData = JSON.parse(currentData);
        parsedData.emailBody = this.emailBody;
        parsedData.emailSubject = this.emailSubject;
        localStorage.setItem('timesheet_validation_data', JSON.stringify(parsedData));
    }
}
  
  private findRelatedTimesheetRow(sheetName: string, issue: ValidationSummaryItem): any {
    if (!this.validatedData[sheetName]) return null;

    // Filter only rows with status not equal to "Valid"
    const invalidRows = this.validatedData[sheetName].filter((row: any) => row.Status != 'Valid');
    console.log(invalidRows, "not valds")
    // Find a row from invalid ones that matches the condition
    return invalidRows.find((row: any) => {
      return (row.Date && issue.Date && row.Date === issue.Date) ||
        (row.Description && issue.Description && row.Description.includes(issue.Description)) ||
        (row.Hours && issue.Hours && row.Hours.toString() === issue.Hours.toString());
    });
  }


  // Reset all validation results
  private resetResults(): void {
    this.validationSummary = [];
    this.validatedData = {};
    this.selectedUser = 0;
    this.emailBody = '';
    this.clearMessage();
  }

  // Show message with timeout
  private showMessage(message: string, type: 'success' | 'error'): void {
    this.clearMessage();
    this.message = message;
    this.messageType = type;

    this.messageTimeout = setTimeout(() => {
      this.clearMessage();
    }, 5000);
  }

  // Clear current message
  private clearMessage(): void {
    if (this.messageTimeout) {
      clearTimeout(this.messageTimeout);
    }
    this.message = '';
    this.messageType = null;
  }

  // Simple email validation
  private validateEmail(email: string): boolean {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }
  get sheetsWithFlags() {
    return Object.keys(this.validatedData || {}).map(sheetName => {
      const flaggedEntries = this.validatedData[sheetName].filter(
        (entry: any) => entry.Flag && entry.Flag.trim() !== ''
      );
      return {
        sheetName,
        flaggedEntries,
        hasFlags: flaggedEntries.length > 0
      };
    });
  }
  getKeyValue(obj: any) {
    return Object.entries(obj).map(([key, value]) => ({ key, value }));
  }
  private saveToStorage(): void {
    const dataToStore = {
      result: this.result,
      fileName: this.fileName,
      validatedData: this.validatedData,
      validationSummary: this.validationSummary,
      selectedUserName: this.selectedUserName,
      emailSubject: this.emailSubject,
      emailBody: this.emailBody
    };
    
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(dataToStore));
  }
private loadFromStorage(): void {
    const storedData = localStorage.getItem(this.STORAGE_KEY);
    if (storedData) {
      try {
        const parsedData = JSON.parse(storedData);
        
        this.result = parsedData.result;
        this.fileName = parsedData.fileName;
        this.validatedData = parsedData.validatedData || {};
        this.validationSummary = parsedData.validationSummary || [];
        this.selectedUserName = parsedData.selectedUserName || '';
        this.emailSubject = parsedData.emailSubject || '';
        this.emailBody = parsedData.emailBody || '';
        
        // Set the first user as selected if none is selected
        const keys = Object.keys(this.validatedData);
        if (keys.length > 0 && !this.selectedUserName) {
          this.selectedUserName = keys[0];
        }
      } catch (e) {
        console.error('Failed to parse stored data', e);
        this.clearStorage();
      }
    }
  }
   private clearStorage(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }

  // Add this method to clear data when needed (e.g., when uploading a new file)
  clearData(): void {
    this.result = null;
    this.fileName = null;
    this.validatedData = {};
    this.validationSummary = [];
    this.selectedUserName = '';
    this.emailSubject = '';
    this.emailBody = '';
    this.clearStorage();
  }
clearSavedData(): void {
  // Clear from storage
  localStorage.removeItem('timesheet_validation_data');
  
  // Reset component state
  this.result = null;
  this.fileName = null;
  this.validatedData = {};
  this.validationSummary = [];
  this.selectedUserName = '';
  
  // Reset email data
  this.emailBody = '';
  this.emailSubject = '';
}
}