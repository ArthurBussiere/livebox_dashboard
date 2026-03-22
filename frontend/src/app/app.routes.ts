import { inject } from '@angular/core';
import { Router, Routes } from '@angular/router';
import { AuthService } from './core/auth.service';

const authGuard = () => {
  const auth = inject(AuthService);
  return auth.isAuthenticated() ? true : inject(Router).createUrlTree(['/login']);
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
