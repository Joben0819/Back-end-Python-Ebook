const express = require('express');
const { spawn } = require('child_process');
const app = express();
const port = 3004;

app.get('/python', (req, res) => {
  const pythonProcess = spawn('python', ['script.py', 'Alice']); // Change 'Alice' to the desired name

  pythonProcess.stdout.on('data', (data) => {
    const response = data.toString(); 
    res.send(response);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    if (code === 0) {
      console.log('Python script executed successfully.');
    } else {
      console.error(`Python script exited with code ${code}`);
    }
  });
});

app.listen(port, () => {
  console.log(`Node.js server is running on http://localhost:${port}`);
});