import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfrimResetPasswordComponent } from './confrim-reset-password.component';

describe('ConfrimResetPasswordComponent', () => {
  let component: ConfrimResetPasswordComponent;
  let fixture: ComponentFixture<ConfrimResetPasswordComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ConfrimResetPasswordComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ConfrimResetPasswordComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
