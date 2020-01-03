// this is the entry point to the application
import ReactForm from "./components/react_form"
import * as ReactDOM from "react-dom"
import * as React from "react"

// This is where webpack will instruct form to be injected into the html
const wrapper = document.getElementById("app");                                                   
wrapper ? ReactDOM.render(<ReactForm/>, wrapper) : false;

