"use client"



export default function Home() {

const token = localStorage.getItem("token")

    return (
        <div>
            <h1>Home {token} </h1>
        </div>
    )
}