const axios = require("axios")

// FastAPI server URL
const FASTAPI_URL = process.env.FASTAPI_URL || "http://127.0.0.1:8000"

function buildErrorMessage(prefix, error) {
    if (error.response?.data?.detail) {
        return `${prefix}: ${error.response.data.detail}`
    }

    if (error.message) {
        return `${prefix}: ${error.message}`
    }

    return prefix
}


// Validate Form
exports.validateForm = async (req, res) => {

    try {

        const response = await axios.post(
            `${FASTAPI_URL}/validate-form`,
            req.body
        )

        res.json(response.data)

    } catch (error) {

        console.error(error)

        res.status(500).json({
            error: buildErrorMessage("Form validation failed", error)
        })

    }

}


// OCR Document
exports.ocr = async (req, res) => {
    const filePath = req.body?.file_path || req.body?.filePath

    if (!filePath) {
        return res.status(400).json({
            error: "file_path is required"
        })
    }

    try {

        const response = await axios.post(
            `${FASTAPI_URL}/ocr`,
            null,
            {
                params: {
                    file_path: filePath
                }
            }
        )

        res.json(response.data)

    } catch (error) {

        console.error(error)

        res.status(500).json({
            error: buildErrorMessage("OCR service failed", error)
        })

    }

}


// AI Assistant
exports.askAssistant = async (req, res) => {
    const question = req.body?.question || req.body?.query || req.body?.prompt

    if (!question) {
        return res.status(400).json({
            error: "question is required"
        })
    }

    try {

        const response = await axios.post(
            `${FASTAPI_URL}/assistant`,
            null,
            {
                params: {
                    question
                }
            }
        )

        res.json(response.data)

    } catch (error) {

        console.error(error)

        res.status(500).json({
            error: buildErrorMessage("AI assistant failed", error)
        })

    }

}


// Translation
exports.translate = async (req, res) => {
    const text = req.body?.text
    const target = req.body?.target || "hi"

    if (!text) {
        return res.status(400).json({
            error: "text is required"
        })
    }

    try {

        const response = await axios.post(
            `${FASTAPI_URL}/translate`,
            null,
            {
                params: {
                    text,
                    target
                }
            }
        )

        res.json(response.data)

    } catch (error) {

        console.error(error)

        res.status(500).json({
            error: buildErrorMessage("Translation failed", error)
        })

    }

}

exports.copilot = async (req, res) => {
    const question = req.body?.question || req.body?.query || req.body?.prompt

    if (!question) {
        return res.status(400).json({
            error: "query is required"
        })
    }

    try {
        const response = await axios.post(
            `${FASTAPI_URL}/assistant`,
            null,
            {
                params: {
                    question
                }
            }
        )

        const answer = response.data?.response || response.data?.answer || ""
        res.json({
            answer,
            raw: response.data
        })
    } catch (error) {
        console.error(error)

        res.status(500).json({
            error: buildErrorMessage("Copilot failed", error)
        })
    }
}
