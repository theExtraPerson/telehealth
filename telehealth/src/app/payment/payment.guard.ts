import { CanActivateFn } from '@angular/router';

export const paymentGuard: CanActivateFn = (route, state) => {
  return true;
};
