const mongoose = require('mongoose');

const dealerSchema = new mongoose.Schema({
    id: { type: Number, required: true, unique: true },
    city: { type: String, required: true },
    state: { type: String, required: true },
    st: { type: String },
    address: { type: String, required: true },
    zip: { type: String },
    lat: { type: Number },
    long: { type: Number },
    full_name: { type: String, required: true },
    short_name: { type: String },
});

module.exports = mongoose.model('Dealership', dealerSchema);
