const express = require("express")
const router = express.Router()

const aiController = require("../controllers/aiController")

router.post("/validate", aiController.validateForm)
router.post("/ocr", aiController.ocr)
router.post("/assistant", aiController.askAssistant)
router.post("/translate", aiController.translate)
router.post("/copilot", aiController.copilot)

module.exports = router
