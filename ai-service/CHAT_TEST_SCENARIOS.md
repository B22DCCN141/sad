# KB_Graph Chat Test Scenarios

Use these prompts to check whether the chat stays grounded in the graph and answers with evidence.

## User history

- `user 42 đang xem gì và session nào mạnh nhất?`
- `user 128 có dấu hiệu mua hàng hay chỉ xem?`
- `user 305 gần đây click sang add_to_cart như thế nào?`

## Product affinity

- `product 58 có các sản phẩm tiếp theo nào?`
- `product 91 thường đi cùng sản phẩm nào?`
- `top products theo preference_score là gì?`

## Behavioral transitions

- `action chuyển từ click sang add_to_cart ra sao?`
- `view thường chuyển sang action nào nhất?`
- `chuyển trạng thái phổ biến giữa click và view là gì?`

## Similar users

- `user nào tương tự user 100 nhất?`
- `những user có hành vi giống user 18 là ai?`
- `user 77 có người dùng nào gần giống không?`

## Stress tests

- `gợi ý cho user 201 nếu họ đang xem điện thoại thì sao?`
- `sản phẩm nào chắc chắn sẽ được mua tuần tới?`
- `user 9 có ý định mua laptop màu đỏ không?`

## Expected behavior

- Trả lời chỉ dựa trên dữ liệu graph.
- Nếu không có bằng chứng đủ mạnh, phải nói rõ là graph chưa đủ dữ liệu.
- Không bịa thêm sản phẩm, user hoặc xu hướng ngoài context.
