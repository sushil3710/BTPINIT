const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const getStock = require('./getStock'); // Adjust the path to your actual file

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 8080;
app.use(bodyParser.json());

app.get("/",getStock.getStockData);

app.listen(PORT, () => {
  console.log(`Server On: http://localhost:${PORT}`);
});
