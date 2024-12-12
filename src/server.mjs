import express from 'express';
import { InfluxDB, Point } from '@influxdata/influxdb-client';
import { getEnvs } from './envs.mjs';
import cors from 'cors';
const ENV = getEnvs();
console.log({ENV});

const app = express();
app.use(cors());
console.log(ENV.INFLUX.HOST);

// 1.2 Initialize DB connection
const DB_CLIENT = new InfluxDB({
    url: ENV.INFLUX.HOST,
    token: ENV.INFLUX.TOKEN
});
const DB_WRITE_POINT = DB_CLIENT.getWriteApi(
    ENV.INFLUX.ORG,
    ENV.INFLUX.BUCKET
);
DB_WRITE_POINT.useDefaultTags({ app: 'db_api' });

// Check InfluxDB connection
app.get('/api/v1/', (_, res) => res.sendStatus(200));

// Endpoint - Write data point to InfluxDB
app.get('/api/v1/embed', async (req, res) => {
    const value = req.query.value;
    if (!value) {
        return res.status(400).send("Missing query parameter 'value'");
    }

    const numeric_value = parseFloat(value);
    if (isNaN(numeric_value)) {
        return res.status(400).send("Invalid value. Please provide a numeric value.");
    }

    try {
        const point = new Point("qparams");
        point.floatField("value", numeric_value);
        DB_WRITE_POINT.writePoint(point); // starts transaction
        await DB_WRITE_POINT.flush(); // end the transaction => save
        res.send(`Value: ${value} written.`);
    } catch (err) {
        console.error(err);
        res.sendStatus(500);
    }
});

// Enpoints - base
app.get('/', (_, res) => res.send('OK'));

// Enpoints - test query params
app.get('/test', (req, res) => {
    console.log(req.query);
    res.send('Received query params!');
});

// Enpoints - Fetch data from InfluxDB (API V1) within the last 30 days
app.get('/api/v1/get-data', async (req, res) => {
    const query = `
        from(bucket: "${ENV.INFLUX.BUCKET}")
        |> range(start: -30d)
        |> filter(fn: (r) => r._measurement == "qparams")
        |> filter(fn: (r) => r._field == "value")
    `;

    try {
        const results = [];
        const DB_READ_API = DB_CLIENT.getQueryApi(ENV.INFLUX.ORG);

        await DB_READ_API.queryRows(query, {
            next(row, tableMeta) {
                const res = tableMeta.toObject(row);
                results.push(res);
            },
            error(error) {
                console.error('Error during query:', error);
                res.status(500).send('Error fetching data from InfluxDB');
            },
            complete() {
                if (results.length === 0) {
                    res.status(404).send('No data found');  // Nếu không có dữ liệu, trả lỗi 404       
                } else {
                    res.json(results);  // Trả về dữ liệu dưới dạng JSON
                }
            },
        });
    } catch (err) {
        console.error('Error in /get-data route:', err);  // Log lỗi nếu có
        res.status(500).send('Error fetching data from InfluxDB');
    }
});

// 2. Start server
app.listen(ENV.PORT, ENV.HOST, () => {
    console.log(`Listening at http://${ENV.HOST}:${ENV.PORT}`);
});