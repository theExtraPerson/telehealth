import { TestBed } from '@angular/core/testing';
import { CanActivateFn } from '@angular/router';

import { doctorPortalGuard } from './doctor-portal.guard';

describe('doctorPortalGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) => 
      TestBed.runInInjectionContext(() => doctorPortalGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
