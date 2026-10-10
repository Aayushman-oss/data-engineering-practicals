// Practical 3: MongoDB operations (run in mongosh)
db.items.insertOne({ name: "laptop", price: 999 });

db.items.find();

db.products.insertMany([
  { name: "phone", price: 500, stock: 10 },
  { name: "tablet", price: 300, stock: 5 },
  { name: "watch", price: 150, stock: 0 }
]);

db.products.find().pretty();
