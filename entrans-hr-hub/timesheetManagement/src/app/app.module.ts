import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { NgApexchartsModule } from 'ng-apexcharts';
import { SharedModule } from '@shared/shared.module';
import { CoreModule } from '@core/core.module';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { provideHotToastConfig } from '@ngneat/hot-toast';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    CommonModule,
    ReactiveFormsModule,
    HttpClientModule,
    BrowserAnimationsModule,
    NgApexchartsModule,
    SharedModule,
    CoreModule
  ],
  providers: [
    provideHotToastConfig({ 
      position: 'top-right', 
      duration: 4000, 
      stacking: 'depth',
      visibleToasts: 4,
      dismissible: true,
      style: { 
        padding: '16px 18px',
        color: '#111827',
        background: '#ffffff',
        borderRadius: '16px',
        boxShadow: '0 12px 40px rgba(0, 0, 0, 0.10)',
        fontWeight: '600',
        fontSize: '15px',
        border: '1px solid rgba(0,0,0,0.06)',
        maxWidth: '380px',
        minWidth: '340px'
      },
      success: { 
        iconTheme: { primary: '#ECFDF3', secondary: '#12B76A' }
      },
      error: { 
        iconTheme: { primary: '#FEF3F2', secondary: '#F04438' }
      },
      info: { 
        iconTheme: { primary: '#EFF8FF', secondary: '#1570EF' }
      },
      warning: { 
        iconTheme: { primary: '#FFF7E6', secondary: '#F79009' }
      }
    })
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
