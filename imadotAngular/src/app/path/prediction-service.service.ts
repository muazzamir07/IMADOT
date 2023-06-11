import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PredictionServiceService {

  private flaskUrl = 'http://127.0.0.1:5000/'; // Flask server URL
  
  constructor(private http: HttpClient) { }

 
  predictionResults(ctFolder: File[], petFolder: File[]): Observable<any> {
    const formData = new FormData();
    for (let i = 0; i < ctFolder.length; i++) {
      if (ctFolder && ctFolder[i].size > 0) {
        formData.append('ctFolder', ctFolder[i], ctFolder[i].name);
      }
    }

    for (let i = 0; i < petFolder.length; i++) {
      if (petFolder && petFolder[i].size > 0) {
        formData.append('petFolder', petFolder[i], petFolder[i].name);
      }
    }
    return this.http.post(this.flaskUrl + '/api/predict', formData, { responseType: 'blob' as 'json', observe: 'response' });    
  }

/*
  predictionResults(ctFolder: File[], petFolder: File[]) {
    console.log("Prediction result service reached");

    const formData = new FormData();
    // formData.append('ctFolder', ctFolder, ctFolder.name);
    for (let i = 0; i < ctFolder.length; i++) {
      if (ctFolder && ctFolder[i].size > 0) {
        formData.append('ctFolder', ctFolder[i], ctFolder[i].name);
      }
    }

    for (let i = 0; i < petFolder.length; i++) {
      if (petFolder && petFolder[i].size > 0) {
        formData.append('petFolder', petFolder[i], petFolder[i].name);
      }
    }
    this.http.post<any>(this.flaskUrl + '/api/predict', formData, { withCredentials: true }).subscribe(
      (response) => {
        // handle response here
        const int_tumor_type = response.int_tumor_type;
        const int_tumor_prob = response.int_tumor_prob;

        // use the image data to display the image
        const blob = new Blob([response], {type: 'image/png'});
        const imageUrl = window.URL.createObjectURL(blob);
        const img = document.createElement('img');
        img.src = imageUrl;
        document.body.appendChild(img);

        console.log("intermediate tumor type")
        console.log(int_tumor_type)
        console.log("intermediate tumor prob")
        console.log(int_tumor_prob)
      },
      (error) => {
        console.log(error);
      }  
    );    
  }
*/

  
  plot3DResults(ctFolder: File[], petFolder: File[]): Observable<any> {
    const formData = new FormData();
    for (let i = 0; i < ctFolder.length; i++) {
      if (ctFolder && ctFolder[i].size > 0) {
        formData.append('ctFolder', ctFolder[i], ctFolder[i].name);
      }
    }

    for (let i = 0; i < petFolder.length; i++) {
      if (petFolder && petFolder[i].size > 0) {
        formData.append('petFolder', petFolder[i], petFolder[i].name);
      }
    }
    return this.http.post(this.flaskUrl + '/api/plot3D', formData);
  }

  /*
    predictionResults(ctFolder: File, petFolder: File) {
      if (ctFolder != null && petFolder != null) {
        console.log("reached prediction service fine");
  
      }
    }
  */
}