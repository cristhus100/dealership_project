const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const Dealership = require('./models/dealer');
const Review = require('./models/review');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const PORT = process.env.PORT || 5000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/dealership';

// Connect to MongoDB
mongoose.connect(MONGO_URI)
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('MongoDB connection error:', err));

// Seed data if empty
async function seedData() {
    const dealerCount = await Dealership.countDocuments();
    if (dealerCount === 0) {
        const dealers = [
            { id: 1, city: "Kansas City", state: "Kansas", st: "KS", address: "1234 Auto Mall Dr", zip: "66101", lat: 39.114, long: -94.627, full_name: "Premier Auto Sales of Kansas City", short_name: "Premier KC" },
            { id: 2, city: "Overland Park", state: "Kansas", st: "KS", address: "5678 Metcalf Ave", zip: "66212", lat: 38.982, long: -94.667, full_name: "Overland Park Luxury Motors", short_name: "OP Luxury" },
            { id: 3, city: "Wichita", state: "Kansas", st: "KS", address: "9101 E Kellogg Dr", zip: "67207", lat: 37.689, long: -97.330, full_name: "Wichita Auto Plaza", short_name: "Wichita Auto" },
            { id: 4, city: "St. Louis", state: "Missouri", st: "MO", address: "4321 Market St", zip: "63101", lat: 38.627, long: -90.199, full_name: "Gateway City Dealership", short_name: "Gateway City" },
            { id: 5, city: "Springfield", state: "Missouri", st: "MO", address: "2468 Glenstone Ave", zip: "65804", lat: 37.209, long: -93.292, full_name: "Springfield Auto Mart", short_name: "Springfield Auto" },
            { id: 6, city: "Kansas City", state: "Missouri", st: "MO", address: "9876 Main St", zip: "64108", lat: 39.084, long: -94.585, full_name: "KC Downtown Auto Sales", short_name: "KC Downtown" },
            { id: 7, city: "Lawrence", state: "Kansas", st: "KS", address: "1111 Massachusetts St", zip: "66044", lat: 38.972, long: -95.235, full_name: "Lawrence Car Company", short_name: "Lawrence Cars" },
            { id: 8, city: "Topeka", state: "Kansas", st: "KS", address: "2222 Kansas Ave", zip: "66603", lat: 39.048, long: -95.678, full_name: "Topeka Auto Center", short_name: "Topeka Auto" },
        ];
        await Dealership.insertMany(dealers);
        console.log('Seed dealers inserted');
    }

    // Clean any reviews with null ids, then seed
    await Review.deleteMany({ id: null });

    const reviewCount = await Review.countDocuments();
    if (reviewCount === 0) {
        const reviews = [
            { id: 1, name: "John D.", dealership: 1, review: "Excellent service and great selection of vehicles. The staff was very helpful throughout the process.", purchase: true, purchase_date: "2025-11-15", car_make: "Toyota", car_model: "Camry", car_year: "2025" },
            { id: 2, name: "Sarah M.", dealership: 1, review: "Found my dream car here! The financing options were flexible and reasonable.", purchase: true, purchase_date: "2026-01-20", car_make: "Honda", car_model: "CR-V", car_year: "2026" },
            { id: 3, name: "Mike R.", dealership: 2, review: "Terrible experience. The car had issues that weren't disclosed.", purchase: true, purchase_date: "2025-09-10", car_make: "BMW", car_model: "X5", car_year: "2024" },
            { id: 4, name: "Emily T.", dealership: 2, review: "Amazing luxury car selection. The sales team really knows their products.", purchase: false },
            { id: 5, name: "David K.", dealership: 3, review: "Fair prices and no pressure sales approach. I would recommend them.", purchase: true, purchase_date: "2026-03-05", car_make: "Ford", car_model: "F-150", car_year: "2026" },
            { id: 6, name: "Lisa W.", dealership: 4, review: "Fantastic services! The maintenance department went above and beyond.", purchase: true, purchase_date: "2025-07-22", car_make: "Chevrolet", car_model: "Equinox", car_year: "2023" },
            { id: 7, name: "Tom H.", dealership: 5, review: "Good value for the price. The used car selection was impressive.", purchase: false },
        ];
        await Review.insertMany(reviews);
        console.log('Seed reviews inserted');
    }
}

app.listen(PORT, () => {
    console.log(`Dealership service running on port ${PORT}`);
    seedData();
});

// ============================================================
// API Routes (lab exacto)
// ============================================================

// Fetch all dealers
app.get('/fetchDealers', async (req, res) => {
    try {
        const dealers = await Dealership.find();
        res.json(dealers);
    } catch (err) {
        res.status(500).json({ error: 'Error fetching dealers' });
    }
});

// Fetch dealers by state
app.get('/fetchDealers/:state', async (req, res) => {
    try {
        const dealers = await Dealership.find({ state: req.params.state });
        res.json(dealers);
    } catch (err) {
        res.status(500).json({ error: 'Error fetching dealers by state' });
    }
});

// Fetch dealer by ID
app.get('/fetchDealer/:id', async (req, res) => {
    try {
        const dealer = await Dealership.findOne({ id: parseInt(req.params.id) });
        if (!dealer) return res.status(404).json({ error: 'Dealer not found' });
        res.json(dealer);
    } catch (err) {
        res.status(500).json({ error: 'Error fetching dealer' });
    }
});

// Fetch all reviews
app.get('/fetchReviews', async (req, res) => {
    try {
        const reviews = await Review.find().sort({ created_at: -1 });
        res.json(reviews);
    } catch (err) {
        res.status(500).json({ error: 'Error fetching reviews' });
    }
});

// Fetch reviews by dealer ID
app.get('/fetchReviews/dealer/:id', async (req, res) => {
    try {
        const reviews = await Review.find({ dealership: parseInt(req.params.id) }).sort({ created_at: -1 });
        res.json(reviews);
    } catch (err) {
        res.status(500).json({ error: 'Error fetching reviews' });
    }
});

// Insert a review
app.post('/insertReview', async (req, res) => {
    try {
        const lastReview = await Review.findOne({ id: { $ne: null } }).sort({ id: -1 });
        const newId = lastReview ? lastReview.id + 1 : 1;

        const review = new Review({
            id: newId,
            name: req.body.name,
            dealership: parseInt(req.body.dealership),
            review: req.body.review,
            purchase: req.body.purchase || false,
            purchase_date: req.body.purchase_date || '',
            car_make: req.body.car_make || '',
            car_model: req.body.car_model || '',
            car_year: req.body.car_year || '',
        });
        await review.save();
        res.status(201).json({ success: true, review });
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

// Insert review (underscore version for lab compatibility)
app.post('/insert_review', async (req, res) => {
    try {
        const lastReview = await Review.findOne({ id: { $ne: null } }).sort({ id: -1 });
        const newId = lastReview ? lastReview.id + 1 : 1;

        const review = new Review({
            id: newId,
            name: req.body.name,
            dealership: parseInt(req.body.dealership),
            review: req.body.review,
            purchase: req.body.purchase || false,
            purchase_date: req.body.purchase_date || '',
            car_make: req.body.car_make || '',
            car_model: req.body.car_model || '',
            car_year: req.body.car_year || '',
        });
        await review.save();
        res.status(201).json({ success: true, review });
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});
