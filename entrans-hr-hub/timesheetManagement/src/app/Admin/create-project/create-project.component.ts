import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ServiceService } from '../Service/service.service';

@Component({
  selector: 'app-create-project',
  templateUrl: './create-project.component.html',
  styleUrls: ['./create-project.component.css']
})
export class CreateProjectComponent implements OnInit {
  projectForm: FormGroup;
  isLoading = false;
  errorMessage: string | null = null;

  allUsers: any[] = [];
  selectedUsers: any[] = [];
  selectedUserIds: number[] = [];

  isDropdownOpen = false;
  isOwnerDropdownOpen = false;
  ownerSearch: string = '';
  selectedOwner: any = null;

  constructor(
    private fb: FormBuilder,
    private projectService: ServiceService,
    private router: Router
  ) {
    this.projectForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      description: ['', [Validators.required, Validators.minLength(10)]],
      owner: ['', Validators.required],
      user_projects: [[]]
    });
  }

  ngOnInit(): void {
    this.getAllUsers();
  }

  getAllUsers(): void {
    this.projectService.getUsers().subscribe({
      next: (res) => {
        this.allUsers = res;
      },
      error: (err) => {
        console.error('Failed to load users', err);
      }
    });
  }

  onSubmit(): void {
    if (this.projectForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = null;

    const payload = {
      ...this.projectForm.value,
      user_projects: this.selectedUsers.map(user => ({
        user: user.id,
        role: 'collaborator'
      }))
    };

    this.projectService.createProject(payload).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/admin']);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.error || 'Failed to create project';
      }
    });
  }

  // User selection methods
  toggleDropdown(): void {
    this.isDropdownOpen = !this.isDropdownOpen;
  }

  toggleUserSelection(user: any): void {
    const index = this.selectedUsers.findIndex(u => u.id === user.id);
    if (index === -1) {
      this.selectedUsers.push(user);
    } else {
      this.selectedUsers.splice(index, 1);
    }
  }

  isUserSelected(userId: number): boolean {
    return this.selectedUsers.some(user => user.id === userId);
  }

  removeUser(userId: number): void {
    this.selectedUsers = this.selectedUsers.filter(user => user.id !== userId);
  }

  // Owner selection methods
  toggleOwnerDropdown(): void {
    this.isOwnerDropdownOpen = !this.isOwnerDropdownOpen;
  }

  selectOwner(user: any): void {
    this.selectedOwner = user;
    this.projectForm.get('owner')?.setValue(user.id);
    this.isOwnerDropdownOpen = false;
  }

  removeOwner(): void {
    this.selectedOwner = null;
    this.projectForm.get('owner')?.setValue(null);
    this.projectForm.get('owner')?.markAsTouched();
  }

  filteredOwners(): any[] {
    if (!this.ownerSearch) return this.allUsers;
    return this.allUsers.filter(user =>
      user.name.toLowerCase().includes(this.ownerSearch.toLowerCase())
    );
  }
}