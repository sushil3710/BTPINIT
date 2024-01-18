
const mongoose = require('mongoose');
const { calculateStartDate } = require('./getDate');


mongoose.connect('mongodb://127.0.0.1:27017/stocks', { useNewUrlParser: true, useUnifiedTopology: true });

  
const stockSchema = new mongoose.Schema({
  index: String,
  open: Number,
  high: Number,
  low: Number,
  close: Number,
  adjclose: Number,
  volume: Number,
  ticker: String,
});

const Stock = mongoose.model('Stock', stockSchema);

// async function getStockData(stock_name, time_period) {

// //const Stock = mongoose.model(stock_name);
// const startDate = calculateStartDate(time_period);
// // const formattedStartDate = startDate.toISOString().split('T')[0];
// // const formattedEndDate = new Date().toISOString().split('T')[0];

// try {
//     const stockData = await Stock.find({
//         ticker: stock_name,
//         $expr: {
//           $gt: [
//             { $toDate: "$index" },  // Convert the 'index' field to a Date object
//             new Date(startDate)
//           ]
//         }
//     });

//     return stockData;
//   } catch (error) {
//     throw error;
//   }
// }



const getStockData = async (req, res) => {
    
    var info = req.params;
    const startDate = calculateStartDate(info.time_period);
    const stockData=0;
    try {
        stockData = await Stock.find({
            ticker: info.stock_name,
            $expr: {
              $gt: [
                { $toDate: "$index" },  // Convert the 'index' field to a Date object
                new Date(startDate)
              ]
            }
        });
    
        return stockData;
      }catch (error) {
        throw error;
      }
  };

module.exports = { getStockData };
