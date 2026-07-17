import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserTimesheetsListComponent } from './user-timesheets-list.component';

describe('UserTimesheetsListComponent', () => {
  let component: UserTimesheetsListComponent;
  let fixture: ComponentFixture<UserTimesheetsListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [UserTimesheetsListComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserTimesheetsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
