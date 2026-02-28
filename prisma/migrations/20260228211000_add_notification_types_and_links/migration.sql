-- CreateEnum
CREATE TYPE "public"."NotificationType" AS ENUM ('SYSTEM', 'AUTO_CANCEL_NO_SHOW', 'USER_CANCELLED_BY_CUSTOMER', 'AUCTION_EXPIRED_UNBOOKED');

-- AlterTable
ALTER TABLE "public"."notifications"
ADD COLUMN "reservationId" INTEGER,
ADD COLUMN "auctionId" INTEGER,
ADD COLUMN "type" "public"."NotificationType" NOT NULL DEFAULT 'SYSTEM';

-- CreateIndex
CREATE INDEX "notifications_type_isRead_createdAt_idx" ON "public"."notifications"("type", "isRead", "createdAt");
CREATE INDEX "notifications_reservationId_idx" ON "public"."notifications"("reservationId");
CREATE INDEX "notifications_auctionId_idx" ON "public"."notifications"("auctionId");

-- AddForeignKey
ALTER TABLE "public"."notifications"
ADD CONSTRAINT "notifications_reservationId_fkey"
FOREIGN KEY ("reservationId") REFERENCES "public"."reservations"("id")
ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "public"."notifications"
ADD CONSTRAINT "notifications_auctionId_fkey"
FOREIGN KEY ("auctionId") REFERENCES "public"."auctions"("id")
ON DELETE SET NULL ON UPDATE CASCADE;
