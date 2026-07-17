import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserTimesheetsComponent } from './user-timesheets.component';

describe('UserTimesheetsComponent', () => {
  let component: UserTimesheetsComponent;
  let fixture: ComponentFixture<UserTimesheetsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [UserTimesheetsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserTimesheetsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
