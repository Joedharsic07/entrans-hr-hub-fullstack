import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TimesheetAutomationComponent } from './timesheet-automation.component';

describe('TimesheetAutomationComponent', () => {
  let component: TimesheetAutomationComponent;
  let fixture: ComponentFixture<TimesheetAutomationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [TimesheetAutomationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TimesheetAutomationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
