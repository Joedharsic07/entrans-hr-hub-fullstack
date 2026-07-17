import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { AuthInterceptorService } from './interceptors/auth.interceptor';
import { AuthGuard } from './guards/auth.guard';
import { SidebarComponent } from './layouts/sidebar/sidebar.component';
import { FooterComponent } from './layouts/footer/footer.component';
import { RouterModule } from '@angular/router';

@NgModule({
  declarations: [
    SidebarComponent,
    FooterComponent
  ],
  imports: [
    CommonModule,
    RouterModule,
    FormsModule
  ],
  providers: [
    AuthGuard,
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptorService, multi: true }
  ],
  exports: [
    SidebarComponent,
    FooterComponent
  ]
})
export class CoreModule {}
