const express = require('express');
const mongoose = require('mongoose');
const app = express();

// MongoDB connection
const mongoURI = "mongodb+srv://HUSSAIN:12340@hussain.m1ofcjp.mongodb.net/myDatabase?retryWrites=true&w=majority";

// Connect to MongoDB
mongoose.connect(mongoURI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log("MongoDB connected successfully!"))
  .catch(err => console.log("MongoDB connection error:", err));

// Test route
app.get('/', (req, res) => {
  res.send('Website is connected to new MongoDB!');
});

// Data model with email
const userSchema = new mongoose.Schema({
  name: String,
  email: String
});

const User = mongoose.model('User', userSchema);

// Add user example route
app.get('/add-user', async (req, res) => {
  try {
    const newUser = new User({ name: "Hussain", email: "humaidiofficial408@gmail.com" });
    await newUser.save();
    res.send("User added to new MongoDB!");
  } catch (err) {
    console.log(err);
    res.status(500).send("Error adding user");
  }
});

// Read users example route
app.get('/users', async (req, res) => {
  try {
    const users = await User.find();
    res.json(users);
  } catch (err) {
    console.log(err);
    res.status(500).send("Error fetching users");
  }
});

const PORT = 3000;
app.listen(PORT, () => console.log(Server running on port ${PORT}));
