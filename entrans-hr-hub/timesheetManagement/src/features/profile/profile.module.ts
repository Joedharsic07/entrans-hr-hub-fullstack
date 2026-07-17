import { NgApexchartsModule } from 'ng-apexcharts';
import { SharedModule } from '@shared/shared.module';
import { CoreModule } from '@core/core.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ProfileRoutingModule } from './profile-routing.module';
import { UserProfileComponent } from './pages/user-profile/user-profile.component';

@NgModule({
  declarations: [
    UserProfileComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    ProfileRoutingModule,
    CoreModule,
    SharedModule,
    NgApexchartsModule
  ]
})
export class ProfileModule { }
