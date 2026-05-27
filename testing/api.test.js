import request from "supertest";

const API = "http://localhost:5000"; 

describe("Testing de la API EduCampus", () => {

  test("El servidor responde correctamente", async () => {
    const response = await request(API).get("/");
    
    expect(response.statusCode).toBe(200);
  });

});