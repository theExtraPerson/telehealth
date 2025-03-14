import { CanActivateFn } from '@angular/router';

export const patientPortalGuard: CanActivateFn = (route, state) => {
  return true;
};
