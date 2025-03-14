import { CanActivateFn } from '@angular/router';

export const doctorPortalGuard: CanActivateFn = (route, state) => {
  return true;
};
