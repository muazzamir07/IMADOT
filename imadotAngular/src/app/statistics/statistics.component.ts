import { HttpClient, HttpErrorResponse, HttpResponse } from '@angular/common/http';
import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { PredictionServiceService } from '../path/prediction-service.service';

@Component({
  selector: 'app-statistics',
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.scss']
})
export class StatisticsComponent implements OnInit {
  /*
    CT_folder: string | null = null;
    PET_folder: string | null = null;
   // plotUrl!: string;
   // input_dir = '../dummyData/A200';
   // imageURL!: string;
  
  //  constructor(private http: HttpClient) { }
    constructor() { }
    
    ngOnInit() {
      //const inputDir = '../dummyData/A200';
      // Set the URL of the API endpoint that returns the plot data
      //this.plotUrl = `/api/plot?input_dir=${this.input_dir}`;
    }
    
    
    //we take CT and PET folder input here and 
    onFileSelected(event: any, folderType: string) {
      const files = event.target.files;
      const fileArr = Array.prototype.slice.call(files);
    
      // Check if all files in folder are DICOM format
      const invalidFiles = fileArr.filter(file => !file.name.endsWith('.dcm'));
      if (invalidFiles.length > 0) {
        alert(`Invalid files in ${folderType} folder. Only DICOM files are allowed.`);
        return;
      }
  
      // Store folder path based on folder type
      if (folderType === 'CT') {
      this.CT_folder = files[0].webkitRelativePath.split(files[0].name)[0];
      } else if (folderType === 'PET') {
        this.PET_folder = files[0].webkitRelativePath.split(files[0].name)[0];
      }
  
    }
    
    //to prediction
    onUpload() {
      // Check if both folders are selected
      if (!this.CT_folder || !this.PET_folder) {
        alert('Please select both CT and PET folders.');
        return;
      }
    
      console.log("onUpload() ok");
  
      if (this.CT_folder.length > 0 && this.PET_folder.length > 0) {
        const CTData = new FormData();
        const PETData = new FormData();
        for (let i = 0; i < this.CT_folder.length; i++) {
          CTData.append("file[]", this.CT_folder[i], this.CT_folder[i].name);
        }
        // Call your service method and pass formData as parameter
        this.myService.uploadFolder(formData).subscribe(result => {
          console.log(result);
        });
      }
  
      // Call prediction class with folder paths
      //this.predictionService.predict(this.CT_folder, this.PET_folder).subscribe(result => {
        // handle result here
      //}, error => {
      //  console.log(error);
      //});
    }
      */

  private ctFolder: File[] | null = null;
  private petFolder: File[] | null = null;
  tumorType!: string;
  tumorProb!: string;
  errorMessage: string | undefined;


  @Output() myimage = new EventEmitter<any>();
  image: any;
  typeDetected: string = "-";
  probDetected: string = "-";
  LateprobDetected: string = "-";

 // Detected_Tumor_Detail: string | undefined;

  constructor(private predictionService: PredictionServiceService) {

  }

  ngOnInit() { }

  onFolderSelected(event: any, folderType: 'CT' | 'PET') {
    const files: FileList | null = event?.target?.files;
    if (!files || !files.length) {
      alert(`Please select a valid ${folderType} folder.`);
      return;
    }

    const allowedExtensions = ['jpg', 'png'];
    const selectedFiles = Array.from(files);
    const selectedFileNames = selectedFiles.map(file => file.name);
    const invalidFiles = selectedFileNames.filter(name => {
      const extension = name.split('.').pop();
      return extension && !allowedExtensions.includes(extension);
    });

    if (invalidFiles.length > 0) {
      alert(`Invalid ${folderType} files: ${invalidFiles.join(', ')}`);
      return;
    }

    if (folderType === 'CT') {
      this.ctFolder = selectedFiles;
    } else if (folderType === 'PET') {
      this.petFolder = selectedFiles;
    }
  }


  onUpload() {
    if (!this.ctFolder || !this.petFolder) {
      alert('Please select valid CT and PET folders.');
      return;
    }

    this.predictionService.predictionResults(this.ctFolder, this.petFolder).subscribe(
      (data: HttpResponse<Blob>) => {
        
        console.log(data);
        if (data.body != null && data.headers.get('tumor_type') != null) {
          this.typeDetected = data.headers.get('tumor_type') ?? "Unknown";
          this.probDetected = data.headers.get('tumor_prob') ?? "Unknown";

          const subtractValue = 0.0;          
          // Convert the string to a number
          const num = parseFloat(this.probDetected);
          
          // Perform the subtraction
          const result = num - subtractValue;
          
          // Convert the result back to a string
          this.probDetected = result.toString();

          this.LateprobDetected = data.headers.get('tumor_prob_late') ?? "Unknown";
          
          const fileReader = new FileReader;
          fileReader.readAsDataURL(data.body);
          fileReader.onloadend = () => {
            if (data.body != null) {
              const file = new File([data.body], "filename.jpg", { type: data.body?.type })
              this.image = [file]
              this.myimage.emit({ photo: fileReader.result, detectedType: this.typeDetected });
              // Access the image element in HTML and set its src attribute to the data URL
              const imgElement = document.getElementById('myImage');
              if (imgElement) {
                imgElement.setAttribute('src', fileReader.result as string);
              }
            }
          }
        
        }
        console.log("Tumor type: ", this.typeDetected);
        console.log("Tumor probability: ", this.probDetected);
/*        
        if (data.body != null && data.headers.get('tumor_type') != null && data.headers.get('tumor_prob') != null) {
          this.typeDetected = data.headers.get('tumor_type') ?? "Unknown";
          this.probDetected = data.headers.get('tumor_prob') ?? "Unknown";
          console.log("+++++++++++RETURNED DATA+++++++++++++")
          console.log(this.typeDetected);
          console.log(this.probDetected);
        }
*/        
      });

    
    console.log("ok");

  }

  on3DPlot() {
    if (!this.ctFolder || !this.petFolder) {
      alert('Please select valid CT and PET folders.');
      return;
    }
    this.predictionService.plot3DResults(this.ctFolder, this.petFolder)
      .subscribe(result => {
      console.log(result.int_tumor_type);
      });
      //;
    console.log("ok 3D plot");
  }

  on3DModel() {

  }

}