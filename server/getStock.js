const mongoose = require('mongoose');
const { calculateStartDate } = require('./getDate');

mongoose.connect('mongodb://127.0.0.1:27017/stocks', { useNewUrlParser: true, useUnifiedTopology: true });



const getAllStockData = async (req, res) => {
  try {
    
    const database = mongoose.connection.db;
    // Get the list of collection names
    const collections = await database.listCollections().toArray();

    // Fetch all documents from each collection
    const allStockData = await Promise.all(
      collections.map(async ({ name }) => {
        const collection = database.collection(name);
        const data = await collection.find({}).toArray(); // Adjust fields as needed
        return { data };
      })
    );

    res.json(allStockData);
  } catch (error) {
    console.error(error);
    // Handle errors and send an appropriate response
    res.status(500).json({ error: 'Internal Server Error' });
  }
};


const getStockData = async (req, res) => {

    try {
        const database = mongoose.connection.db;
        const stockName = req.params.stockName;
        const collectionExists = await database.listCollections({ name: stockName }).hasNext();

        if (!collectionExists) {
            return res.status(404).json({ error: 'Stock not found' });
        }
        const collection = database.collection(stockName);
        const stockData = await collection.find({}).toArray(); // Adjust fields as needed

        res.json({ data: stockData });
    } catch (error) {
        console.error(error);
        // Handle errors and send an appropriate response
        res.status(500).json({ error: 'Internal Server Error' });
    }
};


const getStockDataPeriod = async (req, res) => {
    try {
        const database = mongoose.connection.db;
        const stockName = req.params.stockName;
        const period = req.params.period;

        const collectionExists = await database.listCollections({ name: stockName }).hasNext();

        if (!collectionExists) {
            return res.status(404).json({ error: 'Stock not found' });
        }

        const collection = database.collection(stockName);

        let startDate;

        // Calculate the starting date based on the period
        switch (period.toLowerCase()) {
            case '1day':
                startDate = new Date();
                break;
            case '1week':
                startDate = new Date();
                startDate.setDate(startDate.getDate() - 7);
                break;
            case '1month':
                startDate = new Date();
                startDate.setMonth(startDate.getMonth() - 1);
                break;
            case '1year':
                startDate = new Date();
                startDate.setFullYear(startDate.getFullYear() - 1);
                break;
            case '5years':
                startDate = new Date();
                startDate.setFullYear(startDate.getFullYear() - 5);
                break;
            default:
                return res.status(400).json({ error: 'Invalid period' });
        }

        // Query to find documents with an index value (date) greater than or equal to startDate
        const stockData = await collection.find({
            index: { $gte: new Date(startDate.toISOString()) }
        }).toArray();
        

        res.json({ collection: stockName, data: stockData });
    } catch (error) {
        console.error(error);
        // Handle errors and send an appropriate response
        res.status(500).json({ error: 'Internal Server Error' });
    }
};


module.exports = { getAllStockData,getStockData,getStockDataPeriod};
