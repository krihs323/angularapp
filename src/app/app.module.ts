import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { EmpleadoComponent } from './empleado/empleado.component';
import { FrutaComponent } from './fruta/fruta.component';

@NgModule({
  declarations: [
    AppComponent,
    EmpleadoComponent,
    FrutaComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
