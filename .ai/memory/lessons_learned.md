# Lessons Learned

> บันทึกบทเรียนที่ได้จากการพัฒนาโปรเจค
> เพื่อไม่ให้ทีมทำผิดซ้ำ และให้ AI เรียนรู้จากประสบการณ์ที่ผ่านมา

---

## 💡 Technical Lessons

<!-- เพิ่ม Technical Lessons ที่นี่ -->

---

## 🎯 Process Lessons

### 1. ต้องสร้าง feat/ branch ก่อนทุกครั้งที่เริ่ม feature หรือ refactor

**สถานการณ์**: จุก commit งาน refactor PricingAmount ทับลงบน branch เดิม (`refactor/non-negative-decimal-vo`) โดยไม่ได้สร้าง `feat/` branch ใหม่ตาม branch strategy ที่กำหนดใน `workproject.md`

**บทเรียน**: ทุกครั้งที่เริ่มงานใหม่ ต้องทำตาม workflow นี้เสมอ:
```bash
git checkout develop
git checkout -b feat/<feature-name> develop
# ... implement + test ...
git checkout develop
git merge feat/<feature-name> --no-ff
git push origin develop
git branch -d feat/<feature-name>
git push origin --delete feat/<feature-name>
```

**ผลลัพธ์**: branch history จะสะอาด ติดตามงานแต่ละชิ้นได้ง่าย และป้องกันการ commit ปนกันระหว่าง feature

---

## 🤝 Collaboration Lessons

<!-- เพิ่ม Collaboration Lessons ที่นี่ -->

---

## 🔮 Future Recommendations

<!-- เพิ่ม Recommendations สำหรับอนาคตที่นี่ -->

---

## รูปแบบ Lesson Learned

```markdown
### X. ชื่อบทเรียน

**สถานการณ์**: เกิดอะไรขึ้น

**บทเรียน**: สิ่งที่เรียนรู้

**ผลลัพธ์**: ผลของการนำไปใช้
```
