import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ValidationTimesheetComponent } from './validation-timesheet.component';

describe('ValidationTimesheetComponent', () => {
  let component: ValidationTimesheetComponent;
  let fixture: ComponentFixture<ValidationTimesheetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ValidationTimesheetComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ValidationTimesheetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
