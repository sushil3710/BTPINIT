const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const getStock = require('./getStock'); // Adjust the path to your actual file

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 8080;
app.use(bodyParser.json());

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.get("/get-names/:name", getStock.getNames);
app.get("/get-all-names", getStock.getAllNames);
app.get("/get-all-stock", getStock.getAllStockData);
app.get("/get-stock/:stockName", getStock.getStockData);
app.get("/get-stock/:stockName/:period", getStock.getStockDataPeriod);
app.get("/get-prediction/:stockName", getStock.getPrediction);
app.get("/get-prediction-BoxJen/:stockName", getStock.getPredictionBoxJen);


app.listen(PORT, () => {
  console.log(`Server On: http://localhost:${PORT}`);
});
