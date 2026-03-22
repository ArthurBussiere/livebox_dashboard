export interface DynDNSHostCreate {
  service: string;
  hostname: string;
  username: string;
  password: string;
  enable: boolean; // default: true
}

export interface DynDNSEnableRequest {
  enable: boolean;
}
