export interface CloudinaryResource {
  public_id: string;
  version: number;
  format: string;
  resource_type: 'image' | 'video' | 'raw';
  bytes: number;
  width?: number;
  height?: number;
  duration?: number;
  url: string;
  secure_url: string;
  created_at: string;
  etag?: string;
  placeholder?: boolean;
}

export interface CloudinaryVideoResource extends CloudinaryResource {
  resource_type: 'video';
  duration: number;
  bit_rate?: number;
  frame_rate?: number;
  video?: {
    codec: string;
    bit_rate: number;
    level: number;
    profile: string;
  };
  audio?: {
    codec: string;
    bit_rate: number;
    frequency: number;
    channels: number;
  };
}

export interface CloudinaryImageResource extends CloudinaryResource {
  resource_type: 'image';
  width: number;
  height: number;
}

export interface CloudinaryUploadResponse {
  public_id: string;
  version: number;
  signature: string;
  width?: number;
  height?: number;
  format: string;
  resource_type: string;
  created_at: string;
  tags: string[];
  bytes: number;
  type: string;
  etag: string;
  placeholder: boolean;
  url: string;
  secure_url: string;
  folder?: string;
  original_filename?: string;
  eager?: Array<{
    transformation: string;
    width: number;
    height: number;
    bytes: number;
    format: string;
    url: string;
    secure_url: string;
  }>;
  duration?: number;
  bit_rate?: number;
  frame_rate?: number;
}

export interface CloudinaryTransformation {
  width?: number;
  height?: number;
  crop?: 'fill' | 'fit' | 'scale' | 'crop' | 'thumb' | 'pad' | 'lpad' | 'mpad' | 'limit' | 'mfit';
  quality?: 'auto' | 'auto:best' | 'auto:good' | 'auto:eco' | 'auto:low' | number;
  format?: 'jpg' | 'png' | 'webp' | 'gif' | 'mp4' | 'webm' | 'auto';
  gravity?: 'auto' | 'center' | 'face' | 'faces' | 'body' | 'person' | 'north' | 'south' | 'east' | 'west';
  start_offset?: string; // e.g., '1s', '5%', '10'
  end_offset?: string;
  effect?: string;
  overlay?: string;
  underlay?: string;
  background?: string;
  color?: string;
  border?: string;
  angle?: number;
  opacity?: number;
  radius?: number | 'max';
  flags?: string[];
  raw_transformation?: string;
}

export interface CloudinaryUploadOptions {
  public_id?: string;
  folder?: string;
  resource_type?: 'image' | 'video' | 'raw' | 'auto';
  type?: 'upload' | 'private' | 'authenticated';
  access_mode?: 'public' | 'authenticated';
  tags?: string[];
  transformation?: CloudinaryTransformation | CloudinaryTransformation[];
  eager?: CloudinaryTransformation[];
  quality?: 'auto' | 'auto:best' | 'auto:good' | 'auto:eco' | 'auto:low' | number;
  format?: 'jpg' | 'png' | 'webp' | 'gif' | 'mp4' | 'webm' | 'auto';
  unique_filename?: boolean;
  use_filename?: boolean;
  overwrite?: boolean;
  invalidate?: boolean;
  notification_url?: string;
  eager_notification_url?: string;
  proxy?: string;
  return_delete_token?: boolean;
  metadata?: Record<string, any>;
  context?: Record<string, any>;
  face_coordinates?: string;
  custom_coordinates?: string;
  auto_tagging?: number;
  categorization?: string;
  detection?: string;
  similarity_search?: boolean;
  ocr?: string;
  raw_convert?: string;
  allowed_formats?: string[];
  moderation?: string;
  upload_preset?: string;
  backup?: boolean;
  eval?: string;
  headers?: Record<string, string>;
  callback?: string;
}

export interface CloudinaryError {
  message: string;
  name: string;
  http_code: number;
  error?: {
    message: string;
  };
}

export interface CloudinaryDeleteResponse {
  result: 'ok' | 'not found';
  partial?: boolean;
  deleted?: Record<string, string>;
  deleted_counts?: {
    [key: string]: number;
  };
}

export interface CloudinarySearchResponse {
  total_count: number;
  time: number;
  next_cursor?: string;
  resources: CloudinaryResource[];
}

export interface CloudinaryFolderResponse {
  name: string;
  path: string;
  created_at: string;
  external_id?: string;
}

export interface CloudinaryUrlOptions {
  secure?: boolean;
  format?: string;
  quality?: 'auto' | 'auto:best' | 'auto:good' | 'auto:eco' | 'auto:low' | number;
  transformation?: CloudinaryTransformation | CloudinaryTransformation[];
  sign_url?: boolean;
  auth_token?: string;
  version?: number;
  resource_type?: 'image' | 'video' | 'raw';
  type?: 'upload' | 'private' | 'authenticated' | 'fetch' | 'list';
  crop?: string;
  width?: number;
  height?: number;
  gravity?: string;
  effect?: string;
  overlay?: string;
  underlay?: string;
  background?: string;
  color?: string;
  border?: string;
  angle?: number;
  opacity?: number;
  radius?: number | 'max';
  flags?: string[];
}