import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PptAutomationComponent } from './ppt-automation.component';

describe('PptAutomationComponent', () => {
  let component: PptAutomationComponent;
  let fixture: ComponentFixture<PptAutomationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [PptAutomationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PptAutomationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
