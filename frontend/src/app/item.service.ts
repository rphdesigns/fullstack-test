import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

const API_BASE = (window as any).__API_BASE__ || '';

export interface Item {
  id?: string;
  title: string;
  completed: boolean;
}

@Injectable()
export class ItemService {
  constructor(private http: HttpClient) {}

  list(): Observable<Item[]> {
    return this.http.get<Item[]>(`${API_BASE}/items`);
  }

  create(item: Item): Observable<Item> {
    return this.http.post<Item>(`${API_BASE}/items`, item);
  }

  update(id: string, item: Partial<Item>): Observable<Item> {
    return this.http.put<Item>(`${API_BASE}/items/${id}`, item);
  }

  delete(id: string): Observable<any> {
    return this.http.delete(`${API_BASE}/items/${id}`);
  }
}
