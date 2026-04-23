"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useState } from "react"

export default function Login() {

    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [loading, setLoading] = useState(false)

    const handleLogin = async () => {
        if (!email || !password) {
            alert("Please fill all fields")
            return
        }

        setLoading(true)

        try {
            const res = await fetch("http://localhost:8000/api/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email,
                    password,
                }),
            })

            const data = await res.json()

            if (!res.ok) {
                console.error("Error:", data)
                alert(data.detail || "Login failed")
                setLoading(false)
                return
            }

            // ✅ stocker token JWT
            if (data.access) {
                localStorage.setItem("token", data.access)
            }

            // optionnel refresh token
            if (data.refresh) {
                localStorage.setItem("refresh", data.refresh)
            }

            console.log("Login success:", data)

            // ✅ redirection
            window.location.href = "/home"

        } catch (error) {
            console.error("Network error:", error)
            alert("Server unreachable")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex items-center justify-center h-screen p-5 w-full bg-gradient-to-br from-black via-slate-800 to-blue-950">
            <Card className="h-[600px] w-[500px]">
                <CardHeader className="justify-center items-center">
                    <CardTitle className="text-4xl">Login</CardTitle>
                </CardHeader>

                <CardContent>
                    <div className="space-y-4">

                        <div>
                            <Label htmlFor="email">Email</Label>
                            <Input
                                type="email"
                                id="email"
                                placeholder="EMAIL"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>

                        <div>
                            <Label htmlFor="password">Password</Label>
                            <Input
                                type="password"
                                id="password"
                                placeholder="PASSWORD"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>

                        <Button
                            className="w-full"
                            onClick={handleLogin}
                            disabled={loading}
                        >
                            {loading ? "Loading..." : "Login"}
                        </Button>

                    </div>
                </CardContent>
            </Card>
        </div>
    )
}