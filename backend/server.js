const express = require("express")
const cors = require("cors")
const aiRoutes = require("./routes/aiRoutes")
const aiController = require("./controllers/aiController")

const app = express()
const PORT = process.env.PORT || 5000

app.use(cors())
app.use(express.json())
app.use("/api/ai", aiRoutes)

app.get("/", (req, res) => {
    res.send("Backend is running")
})

// Backward-compatible routes for existing UI code paths.
app.post("/api/validate", aiController.validateForm)
app.post("/copilot", aiController.copilot)

app.listen(PORT, () => {
    console.log(`Backend running on http://localhost:${PORT}`)
})
