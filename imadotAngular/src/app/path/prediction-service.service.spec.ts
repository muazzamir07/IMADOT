import { TestBed } from '@angular/core/testing';

import { PredictionServiceService } from './prediction-service.service';

describe('PredictionServiceService', () => {
  let service: PredictionServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PredictionServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
