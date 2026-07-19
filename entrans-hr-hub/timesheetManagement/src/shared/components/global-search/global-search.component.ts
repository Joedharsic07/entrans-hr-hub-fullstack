import { Component, HostListener, OnInit, ElementRef, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { Router } from '@angular/router';

@Component({
  selector: 'app-global-search',
  templateUrl: './global-search.component.html',
  styleUrls: ['./global-search.component.css']
})
export class GlobalSearchComponent implements OnInit {
  isOpen = false;
  searchQuery = '';
  results: any[] = [];
  isLoading = false;
  
  @ViewChild('searchInput') searchInput!: ElementRef;
  private searchSubject = new Subject<string>();

  constructor(private http: HttpClient, private router: Router) {
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(query => {
      this.performSearch(query);
    });
  }

  ngOnInit(): void {}

  @HostListener('window:keydown.control.k', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) {
    event.preventDefault();
    this.openSearch();
  }
  
  @HostListener('window:keydown.escape', ['$event'])
  handleEscape() {
    this.closeSearch();
  }

  openSearch() {
    this.isOpen = true;
    setTimeout(() => this.searchInput?.nativeElement.focus(), 100);
  }

  closeSearch() {
    this.isOpen = false;
    this.searchQuery = '';
    this.results = [];
  }

  onSearchChange(event: any) {
    this.searchSubject.next(event.target.value);
  }

  performSearch(query: string) {
    if (!query.trim()) {
      this.results = [];
      return;
    }
    
    this.isLoading = true;
    this.http.get(`${environment.apiUrl}/search/?q=${query}`).subscribe({
      next: (data: any) => {
        this.results = data.results;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  navigateToResult(result: any) {
    this.closeSearch();
    // In a real app, map type to specific route
    if (result.type === 'project') {
      this.router.navigate(['/projects', result.id]);
    } else if (result.type === 'leave') {
      this.router.navigate(['/leaves']);
    } else {
      this.router.navigate(['/users']);
    }
  }
}
