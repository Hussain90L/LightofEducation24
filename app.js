const express = require('express');
const mongoose = require('mongoose');
const app = express();

// MongoDB connection
const mongoURI = "mongodb+srv://FubHus:12340@hussain.ghvacfv.mongodb.net/?retryWrites=true&w=majority";

mongoose.connect(mongoURI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log("MongoDB connected successfully!"))
  .catch(err => console.log("MongoDB connection error:", err));

// Test route
app.get('/', (req, res) => {
  res.send('Website is connected to MongoDB!');
});

// Data model with email
const userSchema = new mongoose.Schema({
  name: String,
  email: String
});

const User = mongoose.model('User', userSchema);

// Add user route example
app.get('/add-user', async (req, res) => {
  const newUser = new User({ name: "Hussain", email: "humaidiofficial408@gmail.com" });
  await newUser.save();
  res.send("User with email added to MongoDB!");
});

// Read users route
app.get('/users', async (req, res) => {
  const users = await User.find();
  res.json(users);
});

const PORT = 3000;
app.listen(PORT, () => console.log(Server running on port ${PORT}));
