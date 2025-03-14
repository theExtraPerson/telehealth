import { TestBed } from '@angular/core/testing';

import { PatientPortalService } from './patient-portal.service';

describe('PatientPortalService', () => {
  let service: PatientPortalService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PatientPortalService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
