import {Injectable} from '@angular/core';
//import {Http, Response, Headers} from '@angular/http';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import { HttpClientModule } from '@angular/common/http';
import {map} from 'rxjs/operators';
import {Observable} from 'rxjs/Observable';

@Injectable()
export class PeticionesService  {
    public url: string;
    constructor(
        public http: HttpClient
    )    {
        this.url = 'https://my-json-server.typicode.com/typicode/demo/posts';
    }

    getProductos(): Observable<any> {
        return this.http.get(this.url);
    }

    getPrueba() {
        //Uso de la libreria rxjs operators
        //.pipe(map(res => res.json())); 
        return "Hola mundodo desde el servicio peticiones!!";
    }
}
