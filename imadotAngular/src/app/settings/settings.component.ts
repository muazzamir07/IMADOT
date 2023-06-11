import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent implements OnInit {
  imageURL!: string;

  ngOnInit() {
    const filename = 'making.jpg';
    //this.imageURL = this.getImage(filename);
  }

  constructor() {}
  /*
  constructor(private http: HttpClient) { }

  getImage(filename: string): string {
    this.http.get(`/api/get_image/${filename}`, { responseType: 'blob' })
      .subscribe(response => {
        const reader = new FileReader();
        reader.readAsDataURL(response);
        reader.onloadend = () => {
          if (reader.result instanceof ArrayBuffer) {
            this.imageURL = reader.result.toString();
          }
        }
      });
    return this.imageURL;
  }
*/
}
