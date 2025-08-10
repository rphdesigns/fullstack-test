import { Component, OnInit } from '@angular/core';
import { ItemService, Item } from './item.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent implements OnInit {
  items: Item[] = [];
  newTitle = '';
  editing: {[key:string]: boolean} = {};
  editTitle: {[key:string]: string} = {};

  constructor(private svc: ItemService) {}

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    this.svc.list().subscribe(items => this.items = items);
  }

  add() {
    if (!this.newTitle.trim()) return;
    this.svc.create({title: this.newTitle.trim(), completed: false}).subscribe(() => {
      this.newTitle = '';
      this.refresh();
    });
  }

  startEdit(item: Item) {
    this.editing[item.id!] = true;
    this.editTitle[item.id!] = item.title;
  }

  saveEdit(item: Item) {
    const title = this.editTitle[item.id!];
    this.svc.update(item.id!, {title}).subscribe(() => {
      this.editing[item.id!] = false;
      this.refresh();
    });
  }

  toggle(item: Item) {
    this.svc.update(item.id!, {completed: !item.completed}).subscribe(() => this.refresh());
  }

  remove(item: Item) {
    this.svc.delete(item.id!).subscribe(() => this.refresh());
  }
}
