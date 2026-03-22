import { inject } from '@angular/core';
import { Router, Routes } from '@angular/router';
import { map } from 'rxjs';
import { AuthService } from './core/auth.service';

const authGuard = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (!auth.isAuthenticated()) return router.createUrlTree(['/login']);
  return auth.checkSession().pipe(
    map((valid) => valid || router.createUrlTree(['/login'])),
  );
};

const noAuthGuard = () => {
  const auth = inject(AuthService);
  return auth.isAuthenticated() ? inject(Router).createUrlTree(['/devices']) : true;
};

export const routes: Routes = [
  { path: '', redirectTo: 'devices', pathMatch: 'full' },
  {
    path: 'login',
    canActivate: [noAuthGuard],
    loadComponent: () => import('./features/login/login'),
  },
  {
    path: 'devices',
    canActivate: [authGuard],
    loadComponent: () => import('./features/devices/devices'),
  },
  {
    path: 'wifi',
    canActivate: [authGuard],
    loadComponent: () => import('./features/wifi/wifi'),
  },
  {
    path: 'firewall',
    canActivate: [authGuard],
    loadComponent: () => import('./features/firewall/firewall'),
  },
  {
    path: 'dhcp',
    canActivate: [authGuard],
    loadComponent: () => import('./features/dhcp/dhcp'),
  },
  {
    path: 'dyndns',
    canActivate: [authGuard],
    loadComponent: () => import('./features/dyndns/dyndns'),
  },
  {
    path: 'system',
    canActivate: [authGuard],
    loadComponent: () => import('./features/system/system'),
  },
  {
    path: 'lan',
    canActivate: [authGuard],
    loadComponent: () => import('./features/lan/lan'),
  },
  { path: '**', redirectTo: 'devices' },
];
